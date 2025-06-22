<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class GeoapifyService
{
    protected string $apiKey;
    protected string $geocodeUrl = 'https://api.geoapify.com/v1/geocode/search';
    protected string $routeUrl = 'https://api.geoapify.com/v1/routing';

    public function __construct()
    {
        $this->apiKey = config('services.geoapify.api_key');
        if (empty($this->apiKey)) {
            Log::error('Geoapify API key is not configured. Please check your .env file and config/services.php.');
            // Optionally throw an exception or handle this scenario as per application requirements
        }
    }

    /**
     * Geocode an address string to latitude and longitude.
     *
     * @param string $addressText The address to geocode.
     * @return array|null An array with ['latitude', 'longitude', 'formatted_address', 'confidence'] or null on failure.
     */
    public function geocodeAddress(string $addressText): ?array
    {
        if (empty($this->apiKey)) {
            Log::error('Geoapify geocoding failed: API key missing.');
            return null;
        }

        try {
            $response = Http::timeout(10)->get($this->geocodeUrl, [
                'text' => $addressText,
                'apiKey' => $this->apiKey,
                'format' => 'json',
                'limit' => 1 // We usually want the top result
            ]);

            if ($response->successful() && isset($response->json()['results']) && count($response->json()['results']) > 0) {
                $result = $response->json()['results'][0];
                return [
                    'latitude' => $result['lat'],
                    'longitude' => $result['lon'],
                    'formatted_address' => $result['formatted'],
                    'confidence' => $result['rank']['confidence'] ?? 0,
                    // You can add more fields if needed, e.g., country, city, postcode
                ];
            } else {
                Log::warning('Geoapify geocoding failed or no results for address: ' . $addressText, [
                    'status' => $response->status(),
                    'response' => $response->body()
                ]);
                return null;
            }
        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            Log::error('Geoapify geocoding connection error: ' . $e->getMessage());
            return null;
        } catch (\Exception $e) {
            Log::error('Geoapify geocoding general error: ' . $e->getMessage());
            return null;
        }
    }

    /**
     * Get a route between two sets of coordinates.
     *
     * @param array $startCoords ['lat' => float, 'lon' => float]
     * @param array $endCoords ['lat' => float, 'lon' => float]
     * @param string $mode Travel mode (e.g., 'drive', 'walk', 'bicycle', 'transit'). Defaults to 'drive'.
     * @return array|null Route data from Geoapify or null on failure.
     */
    public function getRoute(array $startCoords, array $endCoords, string $mode = 'drive'): ?array
    {
        if (empty($this->apiKey)) {
            Log::error('Geoapify routing failed: API key missing.');
            return null;
        }

        if (empty($startCoords['lat']) || empty($startCoords['lon']) || empty($endCoords['lat']) || empty($endCoords['lon'])) {
            Log::error('Geoapify routing failed: Invalid start or end coordinates.', compact('startCoords', 'endCoords'));
            return null;
        }

        try {
            $response = Http::timeout(15)->get($this->routeUrl, [
                'waypoints' => implode(',', [$startCoords['lat'], $startCoords['lon']]) . '|' . implode(',', [$endCoords['lat'], $endCoords['lon']]),
                'mode' => $mode,
                'apiKey' => $this->apiKey,
                // 'details' => 'instruction_details' // To get turn-by-turn instructions
                // Add other parameters as needed, e.g., units, lang
            ]);

            if ($response->successful()) {
                return $response->json(); // Return the full Geoapify route response
            } else {
                Log::warning('Geoapify routing failed.', [
                    'status' => $response->status(),
                    'response' => $response->body(),
                    'start' => $startCoords,
                    'end' => $endCoords,
                    'mode' => $mode
                ]);
                return null;
            }
        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            Log::error('Geoapify routing connection error: ' . $e->getMessage());
            return null;
        } catch (\Exception $e) {
            Log::error('Geoapify routing general error: ' . $e->getMessage());
            return null;
        }
    }
} 