<?php

namespace App\Policies;

use App\Models\Booth;
use App\Models\User;
use App\Models\JobFair;
use Illuminate\Auth\Access\Response;

class BoothPolicy
{
    /**
     * Determine whether the user can view any models.
     * User can view booths if they can view the parent job fair.
     */
    public function viewAny(User $user, JobFair $jobFair): bool
    {
        return $user->can('view', $jobFair);
    }

    /**
     * Determine whether the user can view the model.
     * User can view a specific booth if they can view the parent job fair.
     */
    public function view(User $user, Booth $booth): bool
    {
        return $user->can('view', $booth->jobFair);
    }

    /**
     * Determine whether the user can create models.
     * User can create booths if they can update (manage) the parent job fair.
     */
    public function create(User $user, JobFair $jobFair): bool
    {
        return $user->can('update', $jobFair);
    }

    /**
     * Determine whether the user can update the model.
     * User can update a booth if they can update (manage) the parent job fair.
     */
    public function update(User $user, Booth $booth): bool
    {
        return $user->can('update', $booth->jobFair);
    }

    /**
     * Determine whether the user can delete the model.
     * User can delete a booth if they can update (manage) the parent job fair.
     */
    public function delete(User $user, Booth $booth): bool
    {
        return $user->can('update', $booth->jobFair);
    }

    /**
     * Determine whether the user can restore the model.
     */
    public function restore(User $user, Booth $booth): bool
    {
        return $user->can('update', $booth->jobFair);
    }

    /**
     * Determine whether the user can permanently delete the model.
     */
    public function forceDelete(User $user, Booth $booth): bool
    {
        return $user->can('update', $booth->jobFair);
    }
}
