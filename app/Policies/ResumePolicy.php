<?php

namespace App\Policies;

use App\Models\Resume;
use App\Models\User;
use Illuminate\Auth\Access\HandlesAuthorization;

class ResumePolicy
{
    use HandlesAuthorization;

    /**
     * Determine whether the user can view the resume.
     */
    public function view(User $user, Resume $resume): bool
    {
        return $user->id === $resume->user_id;
    }

    /**
     * Determine whether the user can create resumes.
     */
    public function create(User $user): bool
    {
        return true;
    }

    /**
     * Determine whether the user can update the resume.
     */
    public function update(User $user, Resume $resume): bool
    {
        return $user->id === $resume->user_id;
    }

    /**
     * Determine whether the user can delete the resume.
     */
    public function delete(User $user, Resume $resume): bool
    {
        return $user->id === $resume->user_id;
    }
} 