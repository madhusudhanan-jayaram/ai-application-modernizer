package com.example.api.service;

import com.example.api.model.User;
import com.example.api.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.List;
import java.util.Optional;

/**
 * Service class for User business logic.
 */
@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    /**
     * Find all users.
     *
     * @return List of all users
     */
    public List<User> findAll() {
        return userRepository.findAll();
    }

    /**
     * Find user by ID.
     *
     * @param id User ID
     * @return User object or null
     */
    public User findById(Long id) {
        Optional<User> user = userRepository.findById(id);
        return user.orElse(null);
    }

    /**
     * Find users by email.
     *
     * @param email User email
     * @return List of matching users
     */
    public List<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }

    /**
     * Save a user.
     *
     * @param user User object to save
     * @return Saved user
     */
    public User save(User user) {
        return userRepository.save(user);
    }

    /**
     * Delete a user by ID.
     *
     * @param id User ID
     */
    public void deleteById(Long id) {
        userRepository.deleteById(id);
    }

    /**
     * Check if user exists by email.
     *
     * @param email User email
     * @return true if exists, false otherwise
     */
    public boolean existsByEmail(String email) {
        return userRepository.existsByEmail(email);
    }
}
