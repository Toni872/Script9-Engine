import { ApiError } from './api-client';

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.detail ?? error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Error inesperado. Intenta de nuevo.';
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}
