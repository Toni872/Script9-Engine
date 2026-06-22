import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function Pricing() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate('/planes', { replace: true });
  }, [navigate]);

  return null;
}
