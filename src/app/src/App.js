import './App.css';
import { TodoForm } from './components/TodoForm';
import { TodoList } from './components/TodoList';
import { useTodos } from './hooks/useTodos';

export function App() {
  const { todos, isLoading, error, addTodo } = useTodos();

  return (
    <div className="App">
      <TodoList todos={todos} isLoading={isLoading} error={error} />
      <TodoForm onSubmit={addTodo} />
    </div>
  );
}

export default App;
