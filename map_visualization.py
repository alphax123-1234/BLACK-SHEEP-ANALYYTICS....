def create_folium_map(self, df: pd.DataFrame) -> folium.Map:
    """Create interactive Folium map with sentiment markers - LOCKED ON UGANDA"""
    
    # Create base map - LOCKED on Uganda
    m = folium.Map(
        location=[1.3733, 32.2903],  # Uganda center
        zoom_start=7,                 # Shows all of Uganda
        tiles='OpenStreetMap',
        min_zoom=6,                  # Can't zoom out too far
        max_zoom=12,                 # Can't zoom in too far
        max_bounds=True,             # Prevents panning away
        zoom_control=True,           # Still allows zooming
        scrollWheelZoom=True         # Mouse wheel works, but limited
    )
    
    # RESTRICT PAN BOUNDARIES to East Africa
    # These coordinates lock the map to Uganda region
    m.fit_bounds([
        [-5.0, 27.0],   # Southwest corner (bottom-left)
        [5.0, 36.0]     # Northeast corner (top-right)
    ])
    
    # ... rest of your existing code
    # Add markers, circles, etc.
    
    return m
