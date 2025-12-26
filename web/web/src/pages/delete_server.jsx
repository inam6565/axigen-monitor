import React, { useState } from "react";
import { AlertCircle, CheckCircle } from "lucide-react"; // For icons
import { useNavigate } from "react-router-dom"; // For redirection
import API_BASE_URL from "../config/api";


const DeleteServerPage = () => {
  const [hostname, setHostname] = useState(""); // To store the hostname to be deleted
  const [error, setError] = useState(null); // To store error message
  const [success, setSuccess] = useState(false); // To store success message
  const [loading, setLoading] = useState(false); // To handle loading state
  const navigate = useNavigate(); // To redirect after success

  // Handle input changes
  const handleChange = (e) => {
    setHostname(e.target.value);
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); // Show loading state

    try {
      const response = await fetch(`${API_BASE_URL}/delete_server`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ hostname }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Failed to delete server");
      }

      // Success case
      setSuccess(true);
      setTimeout(() => {
        navigate("/servers"); // Redirect to server overview page after success
      }, 2000);
    } catch (err) {
      // Error handling
      setError(err.message);
      setSuccess(false);
    } finally {
      setLoading(false); // Stop loading state
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-2xl font-semibold mb-4">Delete Server</h2>

      {/* Error message */}
      {error && (
        <div className="mb-4 flex items-center text-red-600 bg-red-50 p-3 rounded-md">
          <AlertCircle className="h-5 w-5 mr-2" />
          <span>{error}</span>
        </div>
      )}

      {/* Success message */}
      {success && (
        <div className="mb-4 flex items-center text-green-600 bg-green-50 p-3 rounded-md">
          <CheckCircle className="h-5 w-5 mr-2" />
          <span>Server deleted successfully!</span>
        </div>
      )}

      {/* Form to delete server */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Hostname Input */}
        <div>
          <label htmlFor="hostname" className="block text-sm font-medium text-gray-700">
            Server Hostname (or IP)
          </label>
          <input
            type="text"
            id="hostname"
            name="hostname"
            value={hostname}
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
            className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 ${
              loading ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {loading ? "Deleting Server..." : "Delete Server"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default DeleteServerPage;
