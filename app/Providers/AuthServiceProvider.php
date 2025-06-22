<?php

namespace App\Providers;

use App\Models\Resume;
use App\Policies\ResumePolicy;
use App\Models\JobFair;
use App\Policies\JobFairPolicy;
use App\Models\Booth;
use App\Policies\BoothPolicy;
use Illuminate\Foundation\Support\Providers\AuthServiceProvider as ServiceProvider;
use Illuminate\Support\Facades\Gate;

class AuthServiceProvider extends ServiceProvider
{
    /**
     * The model to policy mappings for the application.
     *
     * @var array<class-string, class-string>
     */
    protected $policies = [
        Resume::class => ResumePolicy::class,
        JobFair::class => JobFairPolicy::class,
        Booth::class => BoothPolicy::class,
    ];

    /**
     * Register any authentication / authorization services.
     */
    public function boot(): void
    {
        $this->registerPolicies();
    }
} 