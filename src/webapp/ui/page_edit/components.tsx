import { v1 as uuidv1 } from "uuid";
import React from "react";
import { Box } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useAuth } from "../login/components";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";
import { Page, PageTemplate } from "../../casualcms/domain/model";
import { ApiErrorUI } from "../errorApi/components";
import { Loader } from "../loader/components";

const Form = withTheme(ChakraUITheme);

export const PageEdit: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [template, setTemplate] = React.useState<PageTemplate | null>(null);
  const [page, setPage] = React.useState<Page | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [params, setParams] = useSearchParams();
  const pagePath = params.get("page") || "";
  const pagePathSplit = pagePath.split("/");
  pagePathSplit.pop();
  const parentPath: string = pagePathSplit.length
    ? pagePathSplit.join("/")
    : "";
  const q = parentPath
    ? new URLSearchParams({ parent: parentPath })
    : new URLSearchParams();

  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadTemplate() {
      if (!page) {
        return;
      }
      const template = await config.api.template.showTemplate(token, page.type);
      // console.log(template);
      template
        .map((tpl: PageTemplate) => setTemplate(tpl))
        .mapErr((err: ApiError) => setError(err));
      // console.log("setIsLoading");
      setIsLoading(false);
    }
    if (page) {
      loadTemplate();
    }
    return () => { setTemplate(null); setError(null); setIsLoading(true) };
  }, [page]);

  React.useEffect(() => {
    async function loadPage() {
      const page = await config.api.page.showPage(token, pagePath || "");
      // console.log(page)
      page
        .map((page: Page) => setPage(page))
        .mapErr((err: ApiError) => setError(err));
    }
    loadPage();
    return () => { setPage(null); setError(null); };
  }, [pagePath]);

  const onsubmit = async (data: any) => {
    if (!page) {
      return;
    }
    const newPage = data.formData;
    await config.api.page.updatePage(token, page.path, newPage);
    navigate(`/admin/pages?${q}`, { replace: true });
  };

  if (isLoading) {
    return <Loader label="loading page and page template..." />;
  }

  return (
    <Box maxW="720px">
      <ApiErrorUI error={error} />

      {template && page && (
        <Form
          schema={template.schema}
          uiSchema={template.uiSchema}
          formData={page}
          // onChange={() => console.log("changed")}
          onSubmit={onsubmit}
          // onError={() => console.log("errors")}
        />
      )}
    </Box>
  );
};
