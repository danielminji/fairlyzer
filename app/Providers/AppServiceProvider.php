<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use App\Services\ResumeParserService;
use App\Services\MailgunService;
// use App\Services\EmailJSService;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        // Register the ResumeParserService
        $this->app->singleton(ResumeParserService::class, function ($app) {
            return new ResumeParserService();
        });
        
        // Register the MailgunService (primary email service)
        $this->app->singleton(MailgunService::class, function ($app) {
            return new MailgunService();
        });
        
        // Register the legacy EmailJSService
        // $this->app->singleton(EmailJSService::class, function ($app) {
        //     return new EmailJSService();
        // });
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        //
    }
}
