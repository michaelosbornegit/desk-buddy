const endpoint = `${import.meta.env.VITE_API_HOST}` ?? '';
const secret = `${import.meta.env.VITE_API_SECRET}` ?? '';

// TODO make this smarter to handle both json and not json
const enrichedFetch = async (
  url: string,
  options = {} as RequestInit,
  throwOnError = true,
  convertToJson = true
) => {
  const response = await fetch(url, {
    ...options,
    headers: { ...options.headers, Authorization: secret },
  });
  if (response.status === 204) return response;
  if (convertToJson) {
    const jsonResponse = await response.json();
    if (response.ok) return jsonResponse;
    if (throwOnError) throw new Error(jsonResponse.message);
    return jsonResponse;
  }
  return response;
};

export const getDogDashboard = () => {
  return enrichedFetch(`${endpoint}/dashboard/dog/two-screens-four-buttons`);
};