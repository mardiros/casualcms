import { expect } from "chai";

import {
  fromHtml,
  defaultModel,
} from "../../../../src/webapp/ui/components/richtext/parser";

describe.only("Convert Html to slate model", () => {
  it("Parse empty textgenerate the empty paragraph", () => {
    const html = fromHtml("");
    expect(html).eql(defaultModel());
  });

  it("Parse paragraph extract the text", () => {
    const html = fromHtml("<html><p>My lazy dog</p></html>");
    expect(html).eql([
      {
        attrs: {},
        children: [
          {
            text: "My lazy dog",
            type: "TEXT",
          },
        ],
        type: "paragraph",
      },
    ]);
  });

  it("Parse paragraph extract bold text", () => {
    const html = fromHtml("<html><p>My <b>lazy</b> dog</p></html>");
    expect(html).eql([
      {
        attrs: {},
        children: [
          {
            text: "My ",
            type: "TEXT",
          },
          {
            attrs: {},
            children: [
              {
                text: "lazy",
                type: "TEXT",
              },
            ],
            type: "strong",
          },
          {
            text: " dog",
            type: "TEXT",
          },
        ],
        type: "paragraph",
      },
    ]);
  });
});
