# migrations/env.py
from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- Alembic 기본 설정 로드 ---
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- 프로젝트 루트(= env.py의 상위 디렉터리의 상위) 를 sys.path에 추가 ---
#   .../question_2_11/migrations/env.py -> parents[1] == .../question_2_11
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# --- 여기서 모델의 Base(metadata) 가져오기 ---
# models.py 에서: Base = declarative_base()
from models import Base  # noqa: E402

# Alembic이 자동으로 테이블 변경을 감지할 때 쓸 메타데이터
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,   # 타입 변경도 감지
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.'"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 타입 변경 감지
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
