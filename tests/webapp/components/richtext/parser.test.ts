import { expect } from "chai";

import {
  fromHtml,
  defaultModel,
} from "../../../../src/webapp/ui/components/richtext/parser";

describe.only("Convert Html to slate model", () => {
  it("Parse empty textgenerate the empty paragraph", () => {
    const mdl = fromHtml("");
    expect(mdl).eql(defaultModel());
  });

  it("Parse paragraph extract the text", () => {
    const mdl = fromHtml("<p>My lazy dog</p>");
    expect(mdl).eql([
      {
        children: [
          {
            text: "My lazy dog",
            bold: undefined,
          },
        ],
        type: "paragraph",
      },
    ]);
  });

  it("Parse paragraph extract bold text", () => {
    const mdl = fromHtml("<p>My <b>lazy</b> dog</p>");
    expect(mdl).eql([
      {
        children: [
          {
            text: "My ",
            bold: undefined,
          },
          {
            text: "lazy",
            bold: true,
          },
          {
            text: " dog",
            bold: undefined,
          },
        ],
        type: "paragraph",
      },
    ]);
  });
});
