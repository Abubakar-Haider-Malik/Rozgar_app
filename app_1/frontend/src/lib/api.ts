import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export const submitServiceRequest = async (text: string) => {
  const response = await axios.post(`${API_URL}/request`, { text, user_id: "demo_user" });
  return response.data;
};

export const fetchDemos = async () => {
  const response = await axios.get(`${API_URL}/demos`);
  return response.data.scenarios;
};
