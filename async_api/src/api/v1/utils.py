from http import HTTPStatus
from typing import Any, Callable, Optional, TypeVar, Union

from fastapi import HTTPException

T = TypeVar('T')
R = TypeVar('R')


def raise_exception_if_not_found(
    data: Union[list[Any], Optional[Any]], error_detail: str
) -> None:
    """
    Raise an HTTPException if the given data is empty or None.

    Args:
        data: A list or single instance of any data type.
        error_detail: A string providing a detailed error message for the exception.

    Raises:
        HTTPException: An exception with status code NOT_FOUND (404) and the provided error detail.
    """
    if not data:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_detail)


def to_response_model(data_list: list[T], response_model: Callable[..., R]) -> list[R]:
    """
    Convert a list of data instances to a list of response model instances.

    Args:
        data_list: A list of data instances to be converted.
        response_model: A callable (e.g., a Pydantic model) that takes keyword arguments and returns an instance
                        of the desired response model.

    Returns:
        A list of response model instances created from the given data instances.
    """
    return [response_model(**vars(item)) for item in data_list]
