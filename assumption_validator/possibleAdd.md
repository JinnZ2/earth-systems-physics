def time_to_red_quadratic(self, window: int = 168) -> Optional[float]:
    """
    Project RED threshold crossing using quadratic fit (acceleration included).
    Returns hours to threshold, or None if moving away.
    """
    vals = self.values()
    if len(vals) < 4:
        return self.time_to_red()  # fallback to linear

    n = min(window, len(vals))
    recent = np.array(vals[-n:], dtype=float)
    x = np.arange(len(recent), dtype=float)
    coeffs = np.polyfit(x, recent, 2)  # a*x² + b*x + c
    
    current = recent[-1]
    rate = coeffs[1] + 2*coeffs[0]*(len(recent)-1)
    accel = 2*coeffs[0]
    
    boundary = REGISTRY.get(self.assumption_id)
    if boundary is None or boundary.red_threshold is None:
        return None
    
    threshold = boundary.red_threshold
    higher_is_worse = boundary.higher_is_worse
    
    # Quadratic: a*t² + rate*t + current = threshold
    # Need roots; solve for t > 0
    a = accel / 2  # because x = t, and a = accel/2
    b = rate
    c = current - threshold
    
    if higher_is_worse:
        # heading toward red if current < threshold AND rate > 0 OR accel > 0
        if current >= threshold:
            return 0.0
        if rate <= 0 and accel <= 0:
            return None  # moving away
    else:
        # lower is worse (pH, etc.)
        if current <= threshold:
            return 0.0
        if rate >= 0 and accel >= 0:
            return None  # moving away
    
    # Solve quadratic: a*t² + b*t + c = 0
    if abs(a) < 1e-12:
        # Linear fallback
        return self.time_to_red()
    
    disc = b*b - 4*a*c
    if disc < 0:
        return None  # no real positive root
    
    sqrt_disc = np.sqrt(disc)
    t1 = (-b + sqrt_disc) / (2*a)
    t2 = (-b - sqrt_disc) / (2*a)
    
    # Pick smallest positive root (the soonest crossing)
    roots = [r for r in [t1, t2] if r > 0]
    if not roots:
        return None
    
    # Convert from per-record steps to hours
    # Assuming records at poll_interval (default 60s)
    record_interval_hours = self.monitor.poll_interval / 3600 if hasattr(self, 'monitor') else 1/60
    return min(roots) * record_interval_hours
