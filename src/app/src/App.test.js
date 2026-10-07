import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { createTodo, fetchTodos } from './api/todosApi';

jest.mock('./api/todosApi');

const todo = (id, description) => ({ id, description, created_at: '2026-01-01T00:00:00+00:00' });

beforeEach(() => {
  jest.resetAllMocks();
});

test('renders todos from the backend', async () => {
  fetchTodos.mockResolvedValue([todo('1', 'Learn Docker')]);

  render(<App />);

  expect(await screen.findByText('Learn Docker')).toBeInTheDocument();
});

test('creates a todo and refreshes the list', async () => {
  fetchTodos.mockResolvedValueOnce([]).mockResolvedValueOnce([todo('1', 'Learn React')]);
  createTodo.mockResolvedValue(todo('1', 'Learn React'));

  render(<App />);
  await screen.findByText(/no todos yet/i);

  userEvent.type(screen.getByLabelText(/todo/i), '  Learn React ');
  userEvent.click(screen.getByRole('button', { name: /add todo/i }));

  expect(await screen.findByText('Learn React')).toBeInTheDocument();
  expect(createTodo).toHaveBeenCalledWith('Learn React');
  expect(fetchTodos).toHaveBeenCalledTimes(2);
  await waitFor(() => expect(screen.getByLabelText(/todo/i)).toHaveValue(''));
});

test('shows an error when the list cannot be loaded', async () => {
  fetchTodos.mockRejectedValue(new Error('Could not reach the server. Please try again.'));

  render(<App />);

  expect(await screen.findByRole('alert')).toHaveTextContent(/could not reach the server/i);
});

test('shows an error when creating a todo fails', async () => {
  fetchTodos.mockResolvedValue([]);
  createTodo.mockRejectedValue(new Error('description is required'));

  render(<App />);
  await screen.findByText(/no todos yet/i);

  userEvent.type(screen.getByLabelText(/todo/i), 'x');
  userEvent.click(screen.getByRole('button', { name: /add todo/i }));

  expect(await screen.findByRole('alert')).toHaveTextContent('description is required');
  expect(fetchTodos).toHaveBeenCalledTimes(1);
});

test('does not submit an empty todo', async () => {
  fetchTodos.mockResolvedValue([]);

  render(<App />);
  await screen.findByText(/no todos yet/i);

  userEvent.click(screen.getByRole('button', { name: /add todo/i }));

  expect(await screen.findByRole('alert')).toHaveTextContent(/please enter a description/i);
  expect(createTodo).not.toHaveBeenCalled();
});
