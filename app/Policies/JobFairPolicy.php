<?php

namespace App\Policies;

use App\Models\JobFair;
use App\Models\User;
use Illuminate\Auth\Access\Response;

class JobFairPolicy
{
    /**
     * Determine whether the user can view any models.
     */
    public function viewAny(User $user): bool
    {
        // Typically, an organizer can view their own job fairs.
        // The controller method already filters by organizer_id for index.
        return $user->tokenCan('organizer'); // Or check for a specific role/permission
    }

    /**
     * Determine whether the user can view the model.
     */
    public function view(User $user, JobFair $jobFair): bool
    {
        return $user->id === $jobFair->organizer_id || $user->tokenCan('admin');
    }

    /**
     * Determine whether the user can create models.
     */
    public function create(User $user): bool
    {
        return $user->tokenCan('organizer'); // Or check for a specific role/permission
    }

    /**
     * Determine whether the user can update the model.
     */
    public function update(User $user, JobFair $jobFair): bool
    {
        return $user->id === $jobFair->organizer_id;
    }

    /**
     * Determine whether the user can delete the model.
     */
    public function delete(User $user, JobFair $jobFair): bool
    {
        return $user->id === $jobFair->organizer_id;
    }

    /**
     * Determine whether the user can restore the model.
     */
    public function restore(User $user, JobFair $jobFair): bool
    {
        // Not typically used for this kind of resource unless soft deletes are heavily used by users.
        return $user->id === $jobFair->organizer_id;
    }

    /**
     * Determine whether the user can permanently delete the model.
     */
    public function forceDelete(User $user, JobFair $jobFair): bool
    {
        return $user->id === $jobFair->organizer_id;
    }
}
