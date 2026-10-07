export function TodoList({ todos, isLoading, error }) {
  return (
    <div>
      <h1>List of TODOs</h1>
      {renderContent({ todos, isLoading, error })}
    </div>
  );
}

function renderContent({ todos, isLoading, error }) {
  if (error) {
    return <p role="alert" className="error">{error}</p>;
  }
  if (isLoading && todos.length === 0) {
    return <p>Loading...</p>;
  }
  if (todos.length === 0) {
    return <p>No TODOs yet. Add one below!</p>;
  }
  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <li key={todo.id}>{todo.description}</li>
      ))}
    </ul>
  );
}
