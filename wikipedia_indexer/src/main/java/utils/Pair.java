package utils;

/**
 * Non-comparable pair.
 */
public final class Pair<U, V> {
	private U first;
	private V second;
	
	public Pair(U first, V second) {
		this.setFirst(first);
		this.setSecond(second);
	}
	
	public static <U, V> Pair<U, V> makePair(U first, V second) {
		return new Pair<U, V>(first, second);
	}
	
	public final U getFirst() {
		return first;
	}

	public final void setFirst(U first) {
		this.first = first;
	}

	public final V getSecond() {
		return second;
	}

	public final void setSecond(V second) {
		this.second = second;
	}

	@Override
	public String toString() {
		return "Pair [first=" + first + ", second=" + second + "]";
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((first == null) ? 0 : first.hashCode());
		result = prime * result + ((second == null) ? 0 : second.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		@SuppressWarnings("unchecked")
		Pair<U, V> other = (Pair<U, V>) obj;
		if (first == null) {
			if (other.first != null)
				return false;
		} else if (!first.equals(other.first))
			return false;
		if (second == null) {
			if (other.second != null)
				return false;
		} else if (!second.equals(other.second))
			return false;
		return true;
	}
}
