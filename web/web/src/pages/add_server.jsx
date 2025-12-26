import React, { useState } from "react";
import { useNavigate } from "react-router-dom"; // For redirection after success
import { AlertCircle } from "lucide-react"; // For error icon
import API_BASE_URL from "../config/api";


const AddServerPage = () => {
  const [formData, setFormData] = useState({
    name: "",
    hostname: "",
    cli_port: "",
    webadmin_port: "",
    username: "",
    password: "",
  });

  const [error, setError] = useState(null); // To store any error messages
  const [loading, setLoading] = useState(false); // To show loading state
  const [success, setSuccess] = useState(false); // To show success message

  const navigate = useNavigate();

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); // Show loading indicator

    try {
      const response = await fetch(`${API_BASE_URL}/add_server`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
        });

      if (!response.ok) {
        throw new Error("Failed to add server");
      }

      setSuccess(true); // Server added successfully
      setTimeout(() => {
        navigate("/servers"); // Redirect to server overview page after successful addition
      }, 2000);
    } catch (err) {
      setError(err.message); // Display error message
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-semibold mb-4">Add New Server</h2>

      {error && (
        <div className="mb-4 flex items-center text-red-600 bg-red-50 p-3 rounded-md">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="mb-4 flex items-center text-green-600 bg-green-50 p-3 rounded-md">
          <span>Server added successfully!</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Server Name */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700">
            Server Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>

        {/* Hostname */}
        <div>
          <label htmlFor="hostname" className="block text-sm font-medium text-gray-700">
            Hostname (or IP)
          </label>
          <input
            type="text"
            id="hostname"
            name="hostname"
            value={formData.hostname}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>

        {/* CLI Port */}
        <div>
          <label htmlFor="cli_port" className="block text-sm font-medium text-gray-700">
            CLI Port
          </label>
          <input
            type="number"
            id="cli_port"
            name="cli_port"
            value={formData.cli_port}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>

        {/* WebAdmin Port */}
        <div>
          <label htmlFor="webadmin_port" className="block text-sm font-medium text-gray-700">
            WebAdmin Port
          </label>
          <input
            type="number"
            id="webadmin_port"
            name="webadmin_port"
            value={formData.webadmin_port}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>

        {/* Username */}
        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Username
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>

        {/* Password */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            required
          />
        </div>

        {/* Submit Button */}
        <div>
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
              loading ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {loading ? "Adding Server..." : "Add Server"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddServerPage;
