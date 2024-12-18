import dataclasses
from abc import ABCMeta
from typing import TypeAlias

ApiErrorType: TypeAlias = "ApiGeneralError | ApiValidationError"


def api_error_factory(response_data: dict) -> ApiErrorType:
    if response_data.get("validation"):
        return ApiValidationError(response_data)

    return ApiGeneralError(response_data)


@dataclasses.dataclass(frozen=True)
class BaseApiError(metaclass=ABCMeta):
    """API のエラーレスポンスを管理する Value Object

    API から返されるエラーレスポンス2種
    1. General エラー: 一般的なエラーで、エラーメッセージを1つだけ持つ
    2. Validation エラー: バリデーション時のエラーで、各フィールドに対するエラーなどエラーメッセージを複数持つ

    各エラーレスポンス JSON のバリデーションを行い、共通化メソッドを実装
    """

    is_general = False
    is_validation = False

    response_data: dict


@dataclasses.dataclass(frozen=True)
class ApiGeneralError(BaseApiError):
    """
    General エラーの JSON schema
    {
        "error": {
            "message": "error message"
        }
    }
    """

    is_general = True

    def __post_init__(self) -> None:
        if not ("error" in self.response_data and "message" in self.response_data["error"]):
            raise ValueError(f"General エラーの JSON schema が正しくありません: {self.response_data}")

    @property
    def message(self) -> str:
        return self.response_data["error"]["message"]


@dataclasses.dataclass(frozen=True)
class ApiValidationError(BaseApiError):
    """
    Validation エラーの JSON schema
    {
        "validation": true,
        "errors": {
            "non_field_error": ["error message1", "error message2", ...],
            "name": ["error message1", "error message2", ...],
            "age": ["error message1", "error message2", ...]
        }
    }
    """

    is_validation = True
    NON_FIELD_ERRORS_KEY = "non_field_error"

    def __post_init__(self) -> None:
        if not (self.response_data.get("validation") and "errors" in self.response_data):
            raise ValueError(f"Validation エラーの JSON schema が正しくありません: {self.response_data}")

    @property
    def non_field_error_messages(self) -> list[str]:
        return self.response_data["errors"].get(self.NON_FIELD_ERRORS_KEY, [])

    @property
    def field_error_messages_dict(self) -> dict[str, list[str]]:
        return {
            field_name: messages
            for field_name, messages in self.response_data["errors"].items()
            if field_name != self.NON_FIELD_ERRORS_KEY
        }
