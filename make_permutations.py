def make_permutations(num_shards=100, shard_size=20000, ):
    from uuid import uuid4

    total_num = shard_size * num_shards
    uids = {uuid4().hex[:10] for _ in range(total_num + 100)}
    uids = list(map(str, uids))[:total_num]
    return uids


def test_files(file_templ='./data/bitid_{:03d}.txt', num_shards=100,
               shard_size=20000):
    import os

    data = []
    for shard_ix in range(num_shards):
        file = os.path.join(file_templ.format(shard_ix))
        with open(file) as f:
            content = f.read().strip()
            content = content.split()
            content = set(content)
        assert len(content) == shard_size
        for other_data in data:
            assert not content & set(other_data)
        data.append(content)

    import pdb
    pdb.set_trace()


def save_permutations(file_templ='./data/bitid_{:03d}.txt', num_shards=100,
                      shard_size=20000):
    import os
    from efficiency.log import fwrite

    all_uids = make_permutations(num_shards=num_shards, shard_size=shard_size)

    for shard_ix in range(num_shards):
        uids = all_uids[shard_ix * shard_size: (shard_ix + 1) * shard_size]
        uids = '\n'.join(uids)
        save_to = os.path.join(file_templ.format(shard_ix))
        fwrite(uids, save_to)


def main():
    import os

    folder = './data/'
    num_shards = 100
    shard_size = 20000

    if not os.path.isdir(folder): os.mkdir(folder)
    file_templ = folder + 'bitid_{:03d}.txt'

    save_permutations(file_templ=file_templ, num_shards=num_shards,
                      shard_size=shard_size)

    test_files(file_templ=file_templ, num_shards=num_shards,
               shard_size=shard_size)


if __name__ == '__main__':
    main()
