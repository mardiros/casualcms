import React from "react";
import { Box, Heading } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../casualcms/domain/ports";
import { useConfig } from "../../config";
import { Draft, PageType } from "../../casualcms/domain/model";
import { ApiErrorUI } from "../layout/error_api";
import { Loader } from "../layout/loader";
import { PageBreadcrumb } from "../layout/breadcrumb";

const Form = withTheme(ChakraUITheme);

export const PageEdit: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  const config = useConfig();
  const token = auth.authenticatedUser?.token || "";
  const [pageType, setPageType] = React.useState<PageType | null>(null);
  const [page, setPage] = React.useState<Draft | null>(null);
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
    async function loadPageType() {
      if (!page) {
        return;
      }
      const rtyp = await config.api.pageType.showPageType(
        token,
        page.meta.type
      );
      // console.log(rtyp);
      rtyp
        .map((typ: PageType) => setPageType(typ))
        .mapErr((err: ApiError) => setError(err));
      // console.log("setIsLoading");
      setIsLoading(false);
    }
    if (page) {
      loadPageType();
    }
    return () => {
      setPageType(null);
      setError(null);
      setIsLoading(true);
    };
  }, [page]);

  React.useEffect(() => {
    async function loadPage() {
      const page = await config.api.page.showDraft(token, pagePath || "");
      // console.log(page)
      page
        .map((page: Draft) => setPage(page))
        .mapErr((err: ApiError) => setError(err));
    }
    if (token) {
      loadPage();
    }
    return () => {
      setPage(null);
      setError(null);
    };
  }, [auth, pagePath]);

  const onsubmit = async (data: any) => {
    if (!page) {
      return;
    }
    const newPage = data.formData;
    await config.api.page.updateDraft(token, page.meta.path, newPage);
    navigate(`/admin/pages?${q}`, { replace: true });
  };

  if (isLoading) {
    return <Loader label="loading page and page type..." />;
  }

  return (
    <Box maxW="720px">
      {page && (
        <>
          <Heading>{page.title}</Heading>
          <PageBreadcrumb page={page} />
        </>
      )}

      <ApiErrorUI error={error} />

      {pageType && page && (
        <Form
          schema={pageType.schema}
          uiSchema={pageType.uiSchema}
          formData={page}
          // onChange={() => console.log("changed")}
          onSubmit={onsubmit}
          // onError={() => console.log("errors")}
        />
      )}
    </Box>
  );
};
