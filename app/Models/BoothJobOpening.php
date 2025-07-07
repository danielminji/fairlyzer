<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class BoothJobOpening extends Model
{
    use HasFactory;

    protected $fillable = [
        'booth_id',
        'organizer_id',
        'job_title',
        'primary_field',
        'description',
        'required_skills_general',
        'required_skills_soft',
        'required_experience_years',
        'required_experience_entries',
        'required_cgpa',
    ];

    protected $casts = [
        'required_skills_general' => 'array',
        'required_skills_soft' => 'array',
    ];

    /**
     * Get the booth that this job opening belongs to.
     */
    public function booth()
    {
        return $this->belongsTo(Booth::class);
    }

    /**
     * Get the organizer (user) who created this job opening.
     */
    public function organizer()
    {
        return $this->belongsTo(User::class, 'organizer_id');
    }

    /**
     * Get the job requirement associated with this job opening.
     */
    public function jobRequirement()
    {
        return $this->belongsTo(JobRequirement::class, 'job_requirement_id');
    }
}
