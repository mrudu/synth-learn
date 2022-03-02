def skew(genome):
    score = 0
    score_list = [score]
    for molecule in genome:
        if molecule == 'C':
            score -= 1
        elif molecule == 'G':
            score += 1
        score_list.append(score)
    return score_list

def hamming_distance(p, q):
    dist = 0
    for i in range(len(p)):
        if p[i] != q[i]:
            dist += 1
    return dist

def approximate_pattern_matching_problem(text, pattern, threshold):
    indices = []
    k = len(pattern)
    for i in range(len(text) - k + 1):
        if hamming_distance(text[i:i+k], pattern) <= threshold:
            indices.append(i)
    return indices

def pattern_count(text, pattern):
    indices = []
    pattern_length = len(pattern)
    for i in range(len(text)- pattern_length+1):
        if text[i: i + pattern_length] == pattern:
            indices.append(str(i))
    return indices

def get_immediate_neighbors(pattern):
    neighbors = set()
    for i in range(len(pattern)):
        nucleotides = ['A', 'C', 'G', 'T']
        nucleotides.remove(pattern[i])
        for n in nucleotides:
            neighbors.add(pattern[0:i]+n+pattern[i+1:])
    return neighbors

def neighborhood(pattern, d):
    neighbors = set()
    neighbors.add(pattern)
    while d > 0:
        for n in neighbors:
            neighbors = neighbors.union(get_immediate_neighbors(n))
        d = d-1
    return neighbors

def find_max_in_dict(dct):
    max_count = 0
    max_word = []
    for word in dct.keys():
        value = dct[word]
        if value > max_count:
            max_count = value
            max_word = [word]
        elif value == max_count:
            max_word.append(word)
    return max_word

def frequent_words_helper(text, k, d, include_rc = False):
    word_count = dict()
    neighbor_map = dict()
    for i in range(len(text)-k+1):
        pattern = text[i:i+k]
        newlyadded = False
        if pattern not in neighbor_map.keys():
            neighbor_map[pattern] = neighborhood(pattern, d)
            newlyadded = True
        for n in neighbor_map[pattern]:
            if not newlyadded or n in word_count.keys():
                word_count[n] += 1
            else:
                word_count[n] = 1
            if not include_rc:
                continue
            rc = reverse_complement(n)
            if rc in word_count.keys():
                word_count[rc] += 1
            else:
                word_count[rc] = 1
    return word_count

def frequent_words_with_mismatches(text, k, d):
    return find_max_in_dict(frequent_words_helper(text, k, d))

def motifEnumeration(text_array, k, d):
    start = False
    motifs = set()
    neighbor_map = dict()
    for text in text_array:
        words = set()
        for i in range(len(text)-k+1):
            pattern = text[i:i+k]
            if pattern not in neighbor_map.keys():
                neighbor_map[pattern] = neighborhood(pattern, d)
            words = words.union(neighbor_map[pattern])
        if not start:
            start = True
            motifs = words
        else:
            motifs = motifs.intersection(words)       
    return list(motifs)

def motifEnumerationAlternative(text_array, k, d):
    text = text_array[0]
    text_array = text_array[1:]
    words = set()
    for i in range(len(text)-k+1):
        motif = text[i:i+k]
        motif_neighbors = neighborhood(motif, d)
        for pattern in motif_neighbors:
            addPattern = True
            for other_text in text_array:
                indices = approximate_pattern_matching_problem(other_text, pattern, d)
                if len(indices) == 0:
                    addPattern = False
                    break
            if addPattern:
                words.add(pattern)
    return list(words)

def frequent_words_with_mismatches_and_rc(text, k, d):            
    return find_max_in_dict(frequent_words_helper(text, k, d, True))

def frequent_words(text, k):
    word_count = dict()
    for i in range(len(text)-k+1):
        word = text[i: i + k]
        if word in word_count.keys():
            word_count[word] = word_count[word] + 1
        else:
            word_count[word] = 1
    return find_max_in_dict(word_count)

def find_clumps(text, k, L, t):
    word_count = dict()
    clumps = []
    for i in range(len(text)-k+1):
        word = text[i:i+k]
        if word in word_count.keys():
            word_count[word] = word_count[word] + 1
        else:
            word_count[word] = 1
        if i+k >= L:
            removed_word = text[i+k-L:i-L+k+k]
            word_count[removed_word] = word_count[removed_word]-1
        if word_count[word] >= t and (word not in clumps):
            clumps.append(word)
    return clumps


def reverse_complement(dna):
    reverse_pattern = ""
    for i in range(len(dna)-1, -1, -1):
        if dna[i] == 'A':
            reverse_pattern += 'T'
        elif dna[i] == 'C':
            reverse_pattern += 'G'
        elif dna[i] == 'G':
            reverse_pattern += 'C'
        else:
            reverse_pattern += 'A'
    return reverse_pattern