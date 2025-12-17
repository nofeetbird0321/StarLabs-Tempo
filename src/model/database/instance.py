# Import required libraries / 导入所需的库
import json  # JSON handling / JSON处理
from typing import Optional, List, Dict  # Type hints / 类型提示
from sqlalchemy import create_engine, Column, Integer, String  # SQLAlchemy ORM / SQLAlchemy对象关系映射
from sqlalchemy.ext.declarative import declarative_base  # Base class for models / 模型的基类
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession  # Async database support / 异步数据库支持
from sqlalchemy.orm import sessionmaker  # Session factory / 会话工厂
from loguru import logger  # Logging library / 日志库

# Base class for database models / 数据库模型的基类
Base = declarative_base()


class Wallet(Base):
    """
    Database model for wallet information
    钱包信息的数据库模型
    
    Security Note / 安全提示:
    - Stores private keys in database (ensure database security) / 在数据库中存储私钥（确保数据库安全）
    - Private keys should be encrypted in production / 私钥在生产环境中应加密
    """
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)  # Unique ID / 唯一ID
    private_key = Column(String, unique=True)  # Ethereum private key (SECURITY SENSITIVE) / 以太坊私钥（安全敏感）
    proxy = Column(String, nullable=True)  # Proxy connection string / 代理连接字符串
    status = Column(String)  # Overall wallet status (pending/completed) / 整体钱包状态（待处理/已完成）
    tasks = Column(String)  # JSON string with tasks / JSON字符串，包含任务


class Database:
    """
    Database management class for wallet and task tracking
    用于钱包和任务跟踪的数据库管理类
    
    Uses SQLite with async support via aiosqlite
    通过aiosqlite使用支持异步的SQLite
    
    Security Note / 安全提示:
    - Database file should have restricted permissions / 数据库文件应具有受限权限
    - Contains sensitive private keys / 包含敏感的私钥
    """
    def __init__(self):
        """
        Initialize database connection
        初始化数据库连接
        """
        # Create async SQLite engine / 创建异步SQLite引擎
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///data/accounts.db",  # Database path / 数据库路径
            echo=False,  # Don't log SQL statements / 不记录SQL语句
        )
        # Create session factory / 创建会话工厂
        self.session = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """
        Initialize database (create tables if they don't exist)
        初始化数据库（如果表不存在则创建）
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.success("Database initialized successfully")

    async def clear_database(self):
        """
        Clear entire database (drops and recreates all tables)
        清除整个数据库（删除并重新创建所有表）
        
        Warning / 警告:
        - This will delete all data / 这将删除所有数据
        - Use with caution / 谨慎使用
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)  # Drop all tables / 删除所有表
            await conn.run_sync(Base.metadata.create_all)  # Recreate tables / 重新创建表
        logger.success("Database cleared successfully")

    async def add_wallet(
        self,
        private_key: str,
        proxy: Optional[str] = None,
        tasks_list: Optional[List[str]] = None,
    ) -> None:
        """
        Добавление нового кошелька

        :param private_key: Приватный ключ кошелька
        :param proxy: Прокси (опционально)
        :param tasks_list: Список названий задач
        """
        # Преобразуем список задач в нужный формат для БД
        tasks = []
        for task in tasks_list or []:
            tasks.append(
                {
                    "name": task,
                    "status": "pending",
                    "index": len(tasks) + 1,  # Добавляем индекс для сохранения порядка
                }
            )

        async with self.session() as session:
            wallet = Wallet(
                private_key=private_key,
                proxy=proxy,
                status="pending",
                tasks=json.dumps(tasks),
            )
            session.add(wallet)
            await session.commit()
            logger.success(f"Added wallet {private_key[:4]}...{private_key[-4:]}")

    async def update_task_status(
        self, private_key: str, task_name: str, new_status: str
    ) -> None:
        """
        Обновление статуса конкретной задачи

        :param private_key: Приватный ключ кошелька
        :param task_name: Название задачи
        :param new_status: Новый статус (pending/completed)
        """
        async with self.session() as session:
            wallet = await self._get_wallet(session, private_key)
            if not wallet:
                logger.error(f"Wallet {private_key[:4]}...{private_key[-4:]} not found")
                return

            tasks = json.loads(wallet.tasks)
            for task in tasks:
                if task["name"] == task_name:
                    task["status"] = new_status
                    break

            wallet.tasks = json.dumps(tasks)

            # Проверяем, все ли задачи выполнены
            if all(task["status"] == "completed" for task in tasks):
                wallet.status = "completed"

            await session.commit()
            logger.info(
                f"Updated task {task_name} to {new_status} for wallet {private_key[:4]}...{private_key[-4:]}"
            )

    async def clear_wallet_tasks(self, private_key: str) -> None:
        """
        Очистка всех задач кошелька

        :param private_key: Приватный ключ кошелька
        """
        async with self.session() as session:
            wallet = await self._get_wallet(session, private_key)
            if not wallet:
                return

            wallet.tasks = json.dumps([])
            wallet.status = "pending"
            await session.commit()
            logger.info(
                f"Cleared all tasks for wallet {private_key[:4]}...{private_key[-4:]}"
            )

    async def update_wallet_proxy(self, private_key: str, new_proxy: str) -> None:
        """
        Обновление прокси кошелька

        :param private_key: Приватный ключ кошелька
        :param new_proxy: Новый прокси
        """
        async with self.session() as session:
            wallet = await self._get_wallet(session, private_key)
            if not wallet:
                return

            wallet.proxy = new_proxy
            await session.commit()
            logger.info(
                f"Updated proxy for wallet {private_key[:4]}...{private_key[-4:]}"
            )

    async def get_wallet_tasks(self, private_key: str) -> List[Dict]:
        """
        Получение всех задач кошелька

        :param private_key: Приватный ключ кошелька
        :return: Список задач с их статусами
        """
        async with self.session() as session:
            wallet = await self._get_wallet(session, private_key)
            if not wallet:
                return []
            return json.loads(wallet.tasks)

    async def get_pending_tasks(self, private_key: str) -> List[str]:
        """
        Получение всех незавершенных задач кошелька

        :param private_key: Приватный ключ кошелька
        :return: Список названий незавершенных задач
        """
        tasks = await self.get_wallet_tasks(private_key)
        return [task["name"] for task in tasks if task["status"] == "pending"]

    async def get_completed_tasks(self, private_key: str) -> List[str]:
        """
        Получение всех завершенных задач кошелька

        :param private_key: Приватный ключ кошелька
        :return: Список названий завершенных задач
        """
        tasks = await self.get_wallet_tasks(private_key)
        return [task["name"] for task in tasks if task["status"] == "completed"]

    async def get_uncompleted_wallets(self) -> List[Dict]:
        """
        Получение списка всех кошельков с невыполненными задачами

        :return: Список кошельков с их данными
        """
        async with self.session() as session:
            from sqlalchemy import select

            query = select(Wallet).filter_by(status="pending")
            result = await session.execute(query)
            wallets = result.scalars().all()

            # Преобразуем в список словарей для удобства использования
            return [
                {
                    "private_key": wallet.private_key,
                    "proxy": wallet.proxy,
                    "status": wallet.status,
                    "tasks": json.loads(wallet.tasks),
                }
                for wallet in wallets
            ]

    async def get_wallet_status(self, private_key: str) -> Optional[str]:
        """
        Получение статуса кошелька

        :param private_key: Приватный ключ кошелька
        :return: Статус кошелька или None если кошелёк не найден
        """
        async with self.session() as session:
            wallet = await self._get_wallet(session, private_key)
            return wallet.status if wallet else None

    async def _get_wallet(
        self, session: AsyncSession, private_key: str
    ) -> Optional[Wallet]:
        """Внутренний метод для получения кошелька по private_key"""
        from sqlalchemy import select

        result = await session.execute(
            select(Wallet).filter_by(private_key=private_key)
        )
        return result.scalar_one_or_none()

    async def add_tasks_to_wallet(self, private_key: str, new_tasks: List[str]) -> None:
        """
        Добавление новых задач к существующему кошельку

        :param private_key: Приватный ключ кошелька
        :param new_tasks: Список новых задач для добавления
        """
        async with self.session() as session:
            wallet = await self._get_wallet(session, private_key)
            if not wallet:
                return

            current_tasks = json.loads(wallet.tasks)
            current_task_names = {task["name"] for task in current_tasks}

            # Добавляем только новые задачи
            for task in new_tasks:
                if task not in current_task_names:
                    current_tasks.append({"name": task, "status": "pending"})

            wallet.tasks = json.dumps(current_tasks)
            wallet.status = (
                "pending"  # Если добавили новые задачи, статус снова pending
            )
            await session.commit()
            logger.info(
                f"Added new tasks for wallet {private_key[:4]}...{private_key[-4:]}"
            )

    async def get_completed_wallets_count(self) -> int:
        """
        Получение количества кошельков, у которых выполнены все задачи

        :return: Количество завершенных кошельков
        """
        async with self.session() as session:
            from sqlalchemy import select, func

            query = (
                select(func.count()).select_from(Wallet).filter_by(status="completed")
            )
            result = await session.execute(query)
            return result.scalar()

    async def get_total_wallets_count(self) -> int:
        """
        Получение общего количества кошельков в базе

        :return: Общее количество кошельков
        """
        async with self.session() as session:
            from sqlalchemy import select, func

            query = select(func.count()).select_from(Wallet)
            result = await session.execute(query)
            return result.scalar()

    async def get_wallet_completed_tasks(self, private_key: str) -> List[str]:
        """
        Получение списка выполненных задач кошелька

        :param private_key: Приватный ключ кошелька
        :return: Список названий выполненных задач
        """
        tasks = await self.get_wallet_tasks(private_key)
        return [task["name"] for task in tasks if task["status"] == "completed"]

    async def get_wallet_pending_tasks(self, private_key: str) -> List[Dict]:
        """
        Получение списка невыполненных задач кошелька

        :param private_key: Приватный ключ кошелька
        :return: Список задач с их индексами и статусами
        """
        tasks = await self.get_wallet_tasks(private_key)
        return [task for task in tasks if task["status"] == "pending"]

    async def get_completed_wallets(self) -> List[Dict]:
        """
        Получение списка всех кошельков с выполненными задачами

        :return: Список кошельков с их данными
        """
        async with self.session() as session:
            from sqlalchemy import select

            query = select(Wallet).filter_by(status="completed")
            result = await session.execute(query)
            wallets = result.scalars().all()

            return [
                {
                    "private_key": wallet.private_key,
                    "proxy": wallet.proxy,
                    "status": wallet.status,
                    "tasks": json.loads(wallet.tasks),
                }
                for wallet in wallets
            ]

    async def get_wallet_tasks_info(self, private_key: str) -> Dict:
        """
        Получение полной информации о задачах кошелька

        :param private_key: Приватный ключ кошелька
        :return: Словарь с информацией о задачах
        """
        tasks = await self.get_wallet_tasks(private_key)
        completed = [task["name"] for task in tasks if task["status"] == "completed"]
        pending = [task["name"] for task in tasks if task["status"] == "pending"]

        return {
            "total_tasks": len(tasks),
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completed_count": len(completed),
            "pending_count": len(pending),
        }

    async def add_wallets_batch(
        self,
        wallet_data: List[Dict],
    ) -> int:
        """
        Пакетное добавление кошельков в базу данных

        :param wallet_data: Список словарей с данными кошельков
                            (private_key, proxy, tasks_list)
        :return: Количество успешно добавленных кошельков
        """
        added_count = 0
        async with self.session() as session:
            try:
                wallets_to_add = []

                for data in wallet_data:
                    private_key = data["private_key"]
                    proxy = data.get("proxy")
                    tasks_list = data.get("tasks_list", [])

                    # Преобразуем список задач в нужный формат для БД
                    tasks = []
                    for task in tasks_list:
                        tasks.append(
                            {
                                "name": task,
                                "status": "pending",
                                "index": len(tasks)
                                + 1,  # Добавляем индекс для сохранения порядка
                            }
                        )

                    wallet = Wallet(
                        private_key=private_key,
                        proxy=proxy,
                        status="pending",
                        tasks=json.dumps(tasks),
                    )
                    wallets_to_add.append(wallet)

                session.add_all(wallets_to_add)
                await session.commit()
                added_count = len(wallets_to_add)
                logger.success(f"Added {added_count} wallets in batch mode")

            except Exception as e:
                await session.rollback()
                logger.error(f"Error in batch adding wallets: {e}")

        return added_count

    async def update_wallets_tasks_batch(self, wallet_tasks_data: List[Dict]) -> int:
        """
        Пакетное обновление задач для нескольких кошельков

        :param wallet_tasks_data: Список словарей с данными {private_key, tasks_list}
        :return: Количество успешно обновленных кошельков
        """
        updated_count = 0
        async with self.session() as session:
            try:
                from sqlalchemy import select

                for data in wallet_tasks_data:
                    private_key = data["private_key"]
                    new_tasks = data["tasks_list"]

                    # Получаем кошелек
                    result = await session.execute(
                        select(Wallet).filter_by(private_key=private_key)
                    )
                    wallet = result.scalar_one_or_none()

                    if not wallet:
                        logger.warning(
                            f"Wallet {private_key[:4]}...{private_key[-4:]} not found for batch task update"
                        )
                        continue

                    # Подготавливаем новые задачи
                    tasks = []
                    for task in new_tasks:
                        tasks.append(
                            {"name": task, "status": "pending", "index": len(tasks) + 1}
                        )

                    # Обновляем задачи и статус
                    wallet.tasks = json.dumps(tasks)
                    wallet.status = "pending"
                    updated_count += 1

                # Сохраняем все изменения одним коммитом
                await session.commit()
                logger.success(
                    f"Updated tasks for {updated_count} wallets in batch mode"
                )

            except Exception as e:
                await session.rollback()
                logger.error(f"Error in batch updating wallet tasks: {e}")

        return updated_count


# # Создание и инициализация БД
# db = Database()
# await db.init_db()

# # Добавление кошелька с задачами
# await db.add_wallet(
#     private_key="0x123...",
#     proxy="http://proxy1.com",
#     tasks_list=["FAUCET", "OKX_WITHDRAW", "TESTNET_BRIDGE"]
# )

# # Обновление статуса задачи
# await db.update_task_status(
#     private_key="0x123...",
#     task_name="FAUCET",
#     new_status="completed"
# )

# # Получение списка незавершенных задач
# pending_tasks = await db.get_pending_tasks("0x123...")

# # Очистка задач кошелька
# await db.clear_wallet_tasks("0x123...")

# # Добавление новых задач к существующему кошельку
# await db.add_tasks_to_wallet(
#     private_key="0x123...",
#     new_tasks=["NEW_TASK1", "NEW_TASK2"]
# )
