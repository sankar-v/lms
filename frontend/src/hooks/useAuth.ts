import { useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
  role: string;
}

export const useAuth = () => {
  const [user] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // TODO: Implement authentication logic
    setLoading(false);
  }, []);

  return { user, loading };
};
