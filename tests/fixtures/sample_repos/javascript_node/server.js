/**
 * Express.js server for user management API.
 */

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Simple in-memory database (for testing)
const users = [];
let userIdCounter = 1;

/**
 * GET /api/users - Get all users
 */
app.get('/api/users', (req, res) => {
  res.status(200).json({
    success: true,
    data: users,
  });
});

/**
 * GET /api/users/:id - Get user by ID
 */
app.get('/api/users/:id', (req, res) => {
  const { id } = req.params;
  const user = users.find(u => u.id === parseInt(id));

  if (!user) {
    return res.status(404).json({
      success: false,
      error: 'User not found',
    });
  }

  res.status(200).json({
    success: true,
    data: user,
  });
});

/**
 * POST /api/users - Create a new user
 */
app.post('/api/users', (req, res) => {
  const { name, email } = req.body;

  // Validation
  if (!name || !email) {
    return res.status(400).json({
      success: false,
      error: 'Name and email are required',
    });
  }

  // Check for duplicate email
  if (users.some(u => u.email === email)) {
    return res.status(409).json({
      success: false,
      error: 'Email already exists',
    });
  }

  const newUser = {
    id: userIdCounter++,
    name,
    email,
    createdAt: new Date().toISOString(),
  };

  users.push(newUser);

  res.status(201).json({
    success: true,
    data: newUser,
  });
});

/**
 * PUT /api/users/:id - Update a user
 */
app.put('/api/users/:id', (req, res) => {
  const { id } = req.params;
  const { name, email } = req.body;

  const user = users.find(u => u.id === parseInt(id));

  if (!user) {
    return res.status(404).json({
      success: false,
      error: 'User not found',
    });
  }

  // Update fields
  if (name) user.name = name;
  if (email) user.email = email;

  res.status(200).json({
    success: true,
    data: user,
  });
});

/**
 * DELETE /api/users/:id - Delete a user
 */
app.delete('/api/users/:id', (req, res) => {
  const { id } = req.params;
  const index = users.findIndex(u => u.id === parseInt(id));

  if (index === -1) {
    return res.status(404).json({
      success: false,
      error: 'User not found',
    });
  }

  const deletedUser = users.splice(index, 1);

  res.status(200).json({
    success: true,
    data: deletedUser[0],
  });
});

/**
 * Error handling middleware
 */
app.use((err, req, res, next) => {
  console.error(err.stack);

  res.status(500).json({
    success: false,
    error: 'Internal server error',
  });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
