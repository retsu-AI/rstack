structure LeaseState where
  generation : Nat
  connected : Bool

def disconnect (s : LeaseState) : LeaseState :=
  { generation := s.generation + 1, connected := false }

def reconnect (s : LeaseState) : LeaseState :=
  { s with connected := true }

def accepts (s : LeaseState) (token : Nat) : Prop :=
  s.connected = true ∧ token = s.generation

theorem disconnected_rejects (s : LeaseState) (token : Nat) :
    ¬ accepts (disconnect s) token := by
  simp [accepts, disconnect]

theorem stale_token_rejected (s : LeaseState) :
    ¬ accepts (reconnect (disconnect s)) s.generation := by
  intro h
  exact (Nat.ne_of_lt (Nat.lt_succ_self s.generation)) h.2

theorem current_token_accepted (s : LeaseState) (h : s.connected = true) :
    accepts s s.generation := by
  exact ⟨h, rfl⟩

#print axioms disconnected_rejects
#print axioms stale_token_rejected
#print axioms current_token_accepted
