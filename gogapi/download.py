import arrow
import xml.etree.ElementTree as ETree


class Download:
    def __init__(self, api, data):
        self.api = api
        self.load_glx(data)

    def load_glx(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.total_size = data["total_size"]
        self.files = [File(self.api, file_data) for file_data in data["files"]]

        # installers
        self.os = data.get("os")
        self.language = data.get("language")
        self.version = data.get("version")

        # bonus_content
        self.bonus_type = data.get("type")
        self.count = data.get("count")

class File(GOGBase):
    securelink = Property("infolink")
    chunklink = Property("infolink")

    filename = Property("chunklist")
    available = Property("chunklist")
    notavailablemsg = Property("chunklist")
    md5 = Property("chunklist")
    timestamp = Property("chunklist")
    chunks = Property("chunklist")

    def __init__(self, api, data):
        super().__init__()
        self.api = api
        self.load_glx(data)

    def load_glx(self, data):
        self.id = str(data["id"])
        self.size = data["size"]
        self.infolink = data["downlink"]

    def load_infolink(self, data):
        self.securelink = data["downlink"]
        self.chunklink = data["checksum"]

    def load_chunklist(self, tree):
        self.filename = tree.attrib["name"]
        self.available = bool(int(tree.attrib["available"]))
        self.notavailablemsg = tree.attrib["notavailablemsg"]
        self.md5 = tree.attrib["md5"]
        self.timestamp = arrow.get(tree.attrib["timestamp"])
        self.chunks = []

        for chunk_elem in tree:
            self.chunks.append(Chunk(
                chunk_id=int(chunk_elem.attrib["id"]),
                start=int(chunk_elem.attrib["from"]),
                end=int(chunk_elem.attrib["to"]),
                method=chunk_elem.attrib["method"],
                digest=chunk_elem.text
            ))

    def update_infolink(self):
        infolink_data = self.api.get_json(self.infolink)
        self.load_infolink(infolink_data)

    def update_chunklist(self):
        xml_text = self.api.get(self.chunklink).text
        tree = ETree.fromstring(xml_text)
        self.load_chunklist(tree)

class Chunk:
    def __init__(self, chunk_id, start, end, method, digest):
        self.id = chunk_id
        self.start = start
        self.end = end
        self.method = method
        self.digest = digest

    def __repr__(self):
        CHUNKFORMAT = \
            "Chunk(chunk_id={}, start={}, end={}, method='{}', digest='{}')"
        return CHUNKFORMAT.format(
            self.id, self.start, self.end, self.method, self.digest)