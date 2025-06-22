<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class JobRequirement extends Model
{
    use HasFactory;

    protected $fillable = [
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
}
