"""答题策略模块"""

from .base import BaseStrategy
from .single import SingleChoiceStrategy
from .multiple import MultipleChoiceStrategy
from .blank import FillBlankStrategy
from .dropdown import DropdownStrategy

__all__ = [
    "BaseStrategy",
    "SingleChoiceStrategy",
    "MultipleChoiceStrategy", 
    "FillBlankStrategy",
    "DropdownStrategy"
]
