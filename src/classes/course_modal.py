import discord

import re
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from src.classes.bot import Bot


class CourseInfo:
    def __init__(
        self,
        course_name: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None
    ):
        self.__course_info = {
            "course_name": discord.ui.TextInput(
                label="강좌 이름(채널명)",
                placeholder="강좌 이름을 입력해주세요.",
                default=course_name,
                required=True,
                max_length=100,
            ),
            "category": discord.ui.TextInput(
                label="mutable category", # 카테고리 목록에 따라 유동적으로 변경
                placeholder="카테고리를 입력해주세요.",
                default=category,
                required=True,
                max_length=32,
            ),
            "description": discord.ui.TextInput(
                label="강좌 설명",
                placeholder="강좌 설명을 입력해주세요.",
                default=description,
                style=discord.TextStyle.long,
                max_length=1024,
                required=True,
            ),
            "agree": discord.ui.TextInput(
                label="강의 진행 규칙을 잘 읽고, 동의하시면 \"동의합니다\"를 입력해주세요.",
                placeholder="동의합니다",
                required=True,
            ),
        }

    @property
    def course_name(self) -> discord.ui.TextInput:
        return self.__course_info['course_name']

    @property
    def category(self) -> discord.ui.TextInput:
        return self.__course_info['category']

    @property
    def description(self) -> discord.ui.TextInput:
        return self.__course_info['description']

    @property
    def agree(self) -> discord.ui.TextInput:
        return self.__course_info['agree']

    def keys(self):
        return self.__course_info.keys()

    def values(self):
        return self.__course_info.values()

    def __iter__(self):
        return iter(self.__course_info)

    def __getitem__(self, key: str):
        return self.__course_info[key].value


class CourseModal(discord.ui.Modal, title="강좌 신청"):
    def __init__(
        self,
        interaction: discord.Interaction["Bot"],
        course_name: str = None,
        category: str = None,
        description: str = None,
        **kwargs
    ):
        super().__init__()
        self.course_info = CourseInfo(course_name, category, description)

        # 카테고리의 목록에 따라 유동적으로 변경
        guild_course_categories = { # OrderedSet처럼 사용
            course.name[:-3]: None
                for course in interaction.guild.categories
                if course.name.endswith("강좌")
        }
        self.course_info.category.label = f"카테고리({', '.join(guild_course_categories.keys())} 등)"

        for item in self.course_info.values():
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction["Bot"]):
        def get_view():
            return CourseModalView(**self.course_info)

        if re.search(r"[^\w\s\-]", self.course_info.course_name.value):
            await interaction.response.send_message("강좌 이름에 `-`를 제외한 특수문자를 사용할 수 없습니다.", view=get_view(), ephemeral=True)
            return

        elif not self.course_info.agree.value == "동의합니다":
            await interaction.response.send_message("강의 진행 규칙에 동의해야 강좌를 만들 수 있습니다.", view=get_view(), ephemeral=True)
            return

        elif discord.utils.get(interaction.guild.channels, name=self.course_info.course_name.value):
            await interaction.response.send_message("이미 같은 이름의 강좌가 존재합니다.", view=get_view(), ephemeral=True)
            return

        course_category = {course.name[:-3]: course for course in interaction.guild.categories if course.name.endswith("강좌")}
        selected_category = course_category.get(self.course_info.category.value) or course_category['기타']

        channel_overwrites = {
            # interaction.guild.default_role = @everyone
            interaction.user: discord.PermissionOverwrite(
                manage_channels=True,                    # 채널 관리하기
                send_messages=True,                      # 메시지 보내기
                manage_threads=True,                     # 스레드 관리하기
                create_public_threads=True,              # 공개 스레드 만들기
                send_messages_in_threads=True,           # 스레드에서 메시지 보내기
                embed_links=True,                        # 링크 첨부
                attach_files=True,                       # 파일 첨부
                manage_messages=True,                    # 메시지 관리
            )
        } | selected_category.overwrites                 # 기존 카테고리 권한 상속

        new_channel = await interaction.guild.create_text_channel(
            name=self.course_info.course_name.value,
            category=selected_category,
            topic=self.course_info.description.value,
            overwrites=channel_overwrites,
        )
        await new_channel.send(f"선생님: {interaction.user.mention}\n")
        await interaction.response.send_message(f"강좌가 만들어졌습니다! 좋은 강의 부탁드려요!\n<#{new_channel.id}>", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction["Bot"], error: Exception) -> None:
        await interaction.response.send_message(
            "강좌를 만들던 도중 에러가 발생하였습니다. 다시 시도해 주세요.",
            view=CourseModalView(**self.course_info),
            ephemeral=True
        )
        error_msg = (
            "Ignoring exception in CourseModal\n"
            f"신청자: {interaction.user}\n"
            f"강좌명: {self.course_info.course_name.value}\n"
            f"카테고리: {self.course_info.category.value}\n"
            f"강좌 설명: {self.course_info.description.value}"
        )
        interaction.client.logger.error(error_msg, exc_info=error)


class CourseModalView(discord.ui.View):
    def __init__(self, **kwargs):
        super().__init__(timeout=None)

        button = discord.ui.Button(
            label="강좌 신청하기" if len(kwargs) == 0 else "다시 신청하기",
            style=discord.ButtonStyle.primary,
            custom_id="course_modal_button" if len(kwargs) == 0 else None,
        )
        button.callback = lambda interaction: interaction.response.send_modal(CourseModal(interaction, **kwargs))
        self.add_item(button)
