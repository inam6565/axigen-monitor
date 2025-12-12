import { createBrowserRouter } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import Domains from "../pages/Domains";
import Accounts from "../pages/Accounts";

const router = createBrowserRouter([
  { path: "/", element: <Dashboard /> },
  { path: "/domains", element: <Domains /> },
  { path: "/accounts/:domainId", element: <Accounts /> },
]);

export default router;
