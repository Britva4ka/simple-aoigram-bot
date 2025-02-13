from . import BaseReplyMarkup


class StartMenuMarkup(BaseReplyMarkup):
    social_media = "🙌🏼 Our Social Media"
    feedback = "📝 Feedbacks"
    faq = "⁉️ FAQ"
    support = "💬 Support"


class CancelActionMarkup(BaseReplyMarkup):
    cancel = "❌ Cancel"


class CancelModeratorActionMarkup(BaseReplyMarkup):
    cancel = "Return to moder menu"


class CancelAdminActionMarkup(BaseReplyMarkup):
    cancel = "Return to admin menu"


class ModeratorMenuMarkup(BaseReplyMarkup):
    broadcast = "Run broadcast"
    list_broadcast = "List of broadcasts"
    edit_messages = "Manage messages"
    edit_social_medias = "Manage Social Medias"
    edit_faq_messages = "Manage FAQ"


class EditMessagesMarkup(BaseReplyMarkup):
    main_menu_message = "Main menu"
    social_media_message = "Social Media"
    feedback_message = "Feedbacks"
    faq_message = "FAQ"
    support_message = "Support"
    support_chat_message = "Chat with support"
    ban_message = "Ban message"
    cancel = CancelModeratorActionMarkup.cancel


class SocialMediasMarkup(BaseReplyMarkup):
    add = "Add social media"
    delete = "Delete social media"
    cancel = CancelModeratorActionMarkup.cancel


class FaqMessagesMarkup(BaseReplyMarkup):
    add = "Add FAQ"
    delete = "Delete FAQ"
    cancel = CancelModeratorActionMarkup.cancel


class AdminMenuMarkup(BaseReplyMarkup):
    moderators_list = "List of moderators"
    ban_list = "List of banned users"
    switch_moderator = "Switch moder status"
    switch_ban = "Switch ban status"
