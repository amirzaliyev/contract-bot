import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from handlers import (
    register_user_handlers,
    register_conversation_handler,
    register_document_handler,
    register_add_template_handler,
    register_template_handler
)
from data import sessionmaker_factory
from data.repositories import (
    TelegramUserRepository,
    DocumentRepository,
    TemplateFieldRepository,
)
from utils import UserValidator
from utils.doc_editor import DocumentService


bot_token = settings.BOT_TOKEN


async def main() -> None:

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Initialize dependencies
    user_repository = TelegramUserRepository(sessionmaker_factory)
    document_repository = DocumentRepository(sessionmaker_factory)
    template_field_repository = TemplateFieldRepository(sessionmaker_factory)
    doc_editor = DocumentService(doc_repository=document_repository)
    user_validator = UserValidator()

    dp = Dispatcher(storage=MemoryStorage())

    # Register handlers
    conversation_router = Router(name="conversation")
    register_conversation_handler(router=conversation_router)

    user_router = Router(name="user")
    register_user_handlers(
        router=user_router,
        user_repository=user_repository,
        user_validator=user_validator,
    )
    document_router = Router(name="contract")
    register_document_handler(
        router=document_router, document_repository=document_repository
    )

    template_router = Router(name="template")
    register_template_handler(
        router=template_router,
        template_field_repository=template_field_repository,
        doc_repository=document_repository,
        doc_editor=doc_editor,
    )

    add_template_router = Router(name="add_template")
    register_add_template_handler(
        router=add_template_router,
        doc_repository=document_repository,
        temp_field_repository=template_field_repository,
    )

    dp.include_routers(
        *[
            conversation_router,
            user_router,
            document_router,
            template_router,
            add_template_router,
        ]
    )

    await dp.start_polling(
        bot, handle_as_tasks=True, tasks_concurrency_limit=5, handle_signals=True
    )


if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())

    except KeyboardInterrupt:
        print("Gracefully shutting down...")
