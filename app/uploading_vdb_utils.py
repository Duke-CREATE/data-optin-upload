import os
import pinecone
import datetime


def generating_vetors(embbedings_df, metadata, netid):

    timestamp = datetime.datetime.now().timestamp()

    n_new_vectors = embbedings_df.shape[0]

    ids = [f"ID-{netid}-{timestamp}-{j}" for j in range(n_new_vectors)]
    embbedings_df["ID"] = ids
    timestamp = str(timestamp).replace(" ", "-")
    vectors = [
        {"id": row["ID"], "values": row["values"], "metadata": metadata}
        for _, row in embbedings_df.iterrows()
    ]

    return vectors, ids
