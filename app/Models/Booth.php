<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Booth extends Model
{
    use HasFactory;

    protected $fillable = [
        'job_fair_id',
        'company_name',
        'booth_number_on_map',
    ];

    protected $casts = [
    ];

    /**
     * Get the job fair that this booth belongs to.
     */
    public function jobFair()
    {
        return $this->belongsTo(JobFair::class);
    }

    /**
     * Get the job openings for this booth.
     */
    public function jobOpenings()
    {
        return $this->hasMany(BoothJobOpening::class);
    }
}
