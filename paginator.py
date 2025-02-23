import discord


class Paginator(discord.ui.View):
    def __init__(self, pages: list, title: str = "Pagination", color=discord.Color.blue()):
        """
        A reusable pagination class that works for both surah lists and surah text.

        :param pages: A list of strings, each representing a page of text.
        :param title: The title of the embed.
        :param color: The color of the embed.
        """
        super().__init__()
        self.pages = pages
        self.current_page = 0
        self.title = title
        self.color = color

        # Update button states based on current page
        self.update_buttons()

    def get_embed(self):
        """Creates an embed for the current page."""
        embed = discord.Embed(
            title=self.title,
            description=self.pages[self.current_page],
            color=self.color
        )
        embed.set_footer(text=f"Page {self.current_page + 1} of {len(self.pages)}")
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary, disabled=True)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handles previous page navigation."""
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handles next page navigation."""
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    def update_buttons(self):
        """Enables or disables buttons based on the current page."""
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1
