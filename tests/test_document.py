from encoded.document import Document, Field


class MyDocument(Document):
    text = Field()


class UpperCaseEncoder:
    def encode(self, value):
        if isinstance(value, str):
            return value.upper()
        else:
            return [v.upper() for v in value]


def test_encode():
    MyDocument.text.set_encoder(UpperCaseEncoder())

    doc = MyDocument(text="hello how")
    assert doc.encode().text.encoded_value == "HELLO HOW"


def test_batch_encode():
    MyDocument.text.set_encoder(UpperCaseEncoder())
    doc1 = MyDocument(text="hello")
    doc2 = MyDocument(text="second item")
    MyDocument.batch_encode([doc1, doc2])

    assert doc1.text.encoded_value == "HELLO"
    assert doc2.text.encoded_value == "SECOND ITEM"


def test_batch_create():
    class AnotherDocument(Document):
        text = Field()
        id = Field()

    docs = AnotherDocument.batch_create(id=[1, 2, 3], text=["a", "b", "c"])
    assert docs[0].id.value == 1
    assert docs[0].text.value == "a"

    assert docs[1].id.value == 2
    assert docs[1].text.value == "b"

    assert docs[2].id.value == 3
    assert docs[2].text.value == "c"
