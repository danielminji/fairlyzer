<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class JobFair extends Model
{
    use HasFactory;

    protected $fillable = [
        'organizer_id',
        'title',
        'description',
        'start_datetime',
        'end_datetime',
        'location',
        'latitude',
        'longitude',
        'formatted_address',
        'location_query',
        'map_image_path',
        'status',
    ];

    /**
     * The attributes that should be cast.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'start_datetime' => 'datetime',
        'end_datetime' => 'datetime',
        'latitude' => 'float',
        'longitude' => 'float',
    ];

    /**
     * Get the organizer that owns the job fair.
     */
    public function organizer()
    {
        return $this->belongsTo(User::class, 'organizer_id');
    }

    /**
     * Get the booths for the job fair.
     */
    public function booths()
    {
        return $this->hasMany(Booth::class);
    }

    /**
     * Get the full URL for the map image.
     *
     * @return string|null
     */
    public function getMapImageUrlAttribute(): ?string
    {
        if ($this->map_image_path) {
            return \Illuminate\Support\Facades\Storage::disk('public')->url($this->map_image_path);
        }
        return null;
    }
}
