import { useState } from 'react';

const MAX_DESCRIPTION_LENGTH = 500;

export function TodoForm({ onSubmit }) {
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmed = description.trim();
    if (!trimmed) {
      setError('Please enter a description.');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await onSubmit(trimmed);
      setDescription('');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h1>Create a ToDo</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="todo">ToDo: </label>
          <input
            id="todo"
            type="text"
            value={description}
            maxLength={MAX_DESCRIPTION_LENGTH}
            disabled={isSubmitting}
            onChange={(event) => setDescription(event.target.value)}
          />
        </div>
        {error && <p role="alert" className="error">{error}</p>}
        <div className="form-actions">
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Adding...' : 'Add ToDo!'}
          </button>
        </div>
      </form>
    </div>
  );
}
