import os
import pinecone


def generating_vetors(embbedings_df, index, metadata):

    stats = index.describe_index_stats()
    n_new_vectors = embbedings_df.shape[0]
    index_size = stats["total_vector_count"]
    ids = [f"ID{i}" for i in range(index_size + 1, index_size + n_new_vectors + 1)]
    embbedings_df["ID"] = ids

    vectors = [
        {"id": row["ID"], "values": row["embedding"], "metadata": metadata}
        for _, row in embbedings_df.iterrows()
    ]

    return vectors
