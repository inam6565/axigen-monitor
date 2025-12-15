// src/pages/PlaceholderPage.jsx
import React from 'react';

const PlaceholderPage = ({ title }) => {
  return (
    <div className="bg-white rounded-xl p-16 text-center shadow-xl shadow-gray-200">
      <h2 className="text-3xl font-bold text-gray-900 mb-2">{title}</h2>
      <p className="text-gray-500 text-lg">This page is under construction</p>
    </div>
  );
};

export default PlaceholderPage;