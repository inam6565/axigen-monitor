import api from "./client";

// GET /servers
export async function getServers() {
  const { data } = await api.get("/servers/");
  return data;
}

// GET /domains/server/<server_id>
export async function getDomainsByServer(serverId) {
  const { data } = await api.get(`/domains/server/${serverId}/`);
  return data;
}

// GET /accounts/domain/<domain_id>
export async function getAccountsByDomain(domainId) {
  const { data } = await api.get(`/accounts/domain/${domainId}/`);
  return data;
}

// GET /summary
export async function getSummary() {
  const { data } = await api.get("/summary/");
  return data;
}