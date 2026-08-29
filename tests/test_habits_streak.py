from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from freezegun import freeze_time

from models.models import Habit
from routes.habits import AlreadyCompletedTodayError, compute_new_streak, increment_streak

TODAY = date(2026, 8, 23)
YESTERDAY = TODAY - timedelta(days=1)


# ─── compute_new_streak (lógica pura, sem mock/DB) ────────────────────────────
def test_primeira_conclusao_streak_vira_1():
    assert compute_new_streak(current_streak=0, last_completed_at=None, today=TODAY) == 1


def test_dia_consecutivo_incrementa():
    assert compute_new_streak(current_streak=5, last_completed_at=YESTERDAY, today=TODAY) == 6


def test_gap_reseta_para_1():
    tres_dias_atras = TODAY - timedelta(days=3)
    assert compute_new_streak(current_streak=10, last_completed_at=tres_dias_atras, today=TODAY) == 1


def test_gap_de_exatos_2_dias_tambem_reseta():
    dois_dias_atras = TODAY - timedelta(days=2)
    assert compute_new_streak(current_streak=10, last_completed_at=dois_dias_atras, today=TODAY) == 1


def test_mesmo_dia_rejeita():
    with pytest.raises(AlreadyCompletedTodayError):
        compute_new_streak(current_streak=5, last_completed_at=TODAY, today=TODAY)


# ─── increment_streak (endpoint, db mockado, freezegun controla "hoje") ───────
@freeze_time("2026-08-23")
def test_endpoint_incrementa_e_commita():
    habit = Habit(id=1, streak=5, last_completed_at=YESTERDAY, owner_id=1)
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = habit

    result = increment_streak(habit_id=1, db=db, current_user=MagicMock(id=1))

    assert result.streak == 6
    assert result.last_completed_at == TODAY
    db.commit.assert_called_once()


@freeze_time("2026-08-23")
def test_endpoint_retorna_409_se_ja_concluido_hoje():
    habit = Habit(id=1, streak=5, last_completed_at=TODAY, owner_id=1)
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = habit

    with pytest.raises(HTTPException) as exc:
        increment_streak(habit_id=1, db=db, current_user=MagicMock(id=1))
    assert exc.value.status_code == 409


def test_endpoint_404_se_habito_nao_encontrado():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        increment_streak(habit_id=999, db=db, current_user=MagicMock(id=1))
    assert exc.value.status_code == 404
