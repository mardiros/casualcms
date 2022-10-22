import { expect } from "chai";

import { fromHtml, emptyModel } from "../../../../src/webapp/ui/components/richtext/parser";

describe.only("Convert Html to slate model", () => {
  it("Parse empty textgenerate the empty paragraph", () => {
    const html = fromHtml("");
    expect(html).eql(emptyModel())
  });
});
