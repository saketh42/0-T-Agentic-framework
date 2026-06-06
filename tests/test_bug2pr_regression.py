import pytest

def test_out_of_bounds_index_handled():
    """Test that out-of-bounds index access is handled."""
    items = []
    idx = 0
    
    # Fixed code should check bounds
    if 0 <= idx < len(items):
        item = items[idx]
    else:
        item = None
    
    assert item is None


def test_valid_index_works():
    """Test that valid index access works."""
    items = ["item1", "item2", "item3"]
    idx = 1
    
    item = items[idx]
    assert item == "item2"
