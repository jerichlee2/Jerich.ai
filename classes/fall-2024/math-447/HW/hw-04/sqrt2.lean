import data.real.irrational

theorem sqrt_two_irrational : irrational (real.sqrt 2) :=
begin
  -- Assume that sqrt(2) is rational
  rintros ⟨a, b, hcoprime, h⟩,
  -- Square both sides
  have h_sq : 2 = (a ^ 2) / (b ^ 2),
  { rw [← h, real.sqrt_eq_rpow], field_simp },
  -- Cross-multiply to get rid of the fraction
  have h_mul : 2 * (b ^ 2) = a ^ 2,
  { rw ← eq_div_iff_mul_eq h_sq, field_simp },
  -- Show that a must be even
  have ha_even : even a,
  { apply nat.even_of_mod_eq_zero, sorry },
  -- Since a is even, let a = 2k for some k
  obtain ⟨k, ha⟩ := ha_even,
  rw [ha, pow_two, mul_assoc] at h_mul,
  -- Simplify and show b must be even
  have hb_even : even b,
  { apply nat.even_of_mod_eq_zero, sorry },
  -- Contradiction, since a and b are both even
  exact hcoprime (nat.gcd_eq_one_of_coprime hcoprime).symm,
end